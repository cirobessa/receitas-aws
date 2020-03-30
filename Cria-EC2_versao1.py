import os
import time
import boto
import boto.manage.cmdshell

### Faz o Lancamento de 1 instancia em US-EAST-1 com image do UBUNTU 18.04

def launch_instance(ami='ami-07ebfd5b3428b6f4d',
                    instance_type='t2.micro',
                    key_name='paws',
                    key_extension='.pem',
                    key_dir='~/.ssh',
                    group_name='paws',
                    ssh_port=22,
                    cidr='0.0.0.0/0',
                    tag='paws',
                    user_data=None,
                    cmd_shell=True,
                    login_user='ubuntu',
                    ssh_passwd=None):


    cmd = None
    ec2 = boto.connect_ec2()

    # Verifique se o par de chaves especificado já existe.
    # Se recebermos novamente um erro InvalidKeyPair.NotFound do EC2,
    # significa que não existe e precisamos criá-lo.
    try:
        key = ec2.get_all_key_pairs(keynames=[key_name])[0]
    except ec2.ResponseError, e:
        if e.code == 'InvalidKeyPair.NotFound':
            print
            'Creating keypair: %s' % key_name
            # Cria uma chave SSH para usar ao fazer login em instâncias.
            key = ec2.create_key_pair(key_name)

            # A AWS armazenará a chave pública, mas a chave privada é
            # gerada e retornada e precisa ser armazenado localmente.
            # O método save também chmod o arquivo para proteger
            # sua chave privada.
            key.save(key_dir)
        else:
            raise

    # Verifique se o "Security Group" especificado já existe.
    # Se recebermos novamente um erro InvalidGroup.NotFound do EC2,
    # significa que não existe e precisamos criá-lo.
    try:
        group = ec2.get_all_security_groups(groupnames=[group_name])[0]
    except ec2.ResponseError, e:
        if e.code == 'InvalidGroup.NotFound':
            print
            'Creating Security Group: %s' % group_name
            # Create a security group to control access to instance via SSH.
            group = ec2.create_security_group(group_name,
                                              'A group that allows SSH access')
        else:
            raise


    # Adicione uma regra ao "Security Group" para autorizar o tráfego SSH
    # na porta especificada.
    try:
        group.authorize('tcp', ssh_port, ssh_port, cidr)
    except ec2.ResponseError, e:
        if e.code == 'InvalidPermission.Duplicate':
            print
            'Security Group: %s Ja Autorizado' % group_name
        else:
            raise


    # Agora inicia a instância. O método run_instances
    # tem muitos parâmetros, mas é tudo o que precisamos
    # por enquanto.
    reservation = ec2.run_instances(ami,
                                    key_name=key_name,
                                    security_groups=[group_name],
                                    instance_type=instance_type,
                                    user_data=user_data)

    # Encontre o objeto Instância real dentro do objeto Reserva
    # retornado por EC2.

    instance = reservation.instances[0]

    # A instância foi lançada, mas ainda não está pronta.
    # corrida. Vamos aguardar que seu estado mude para 'running'.

    print
    'Esperando pela Instancia'
    while instance.state != 'running':
        print
        '.'
        time.sleep(5)
        instance.update()
    print
    'done'


    # Vamos marcar a instância com o rótulo especificado para que possamos
    # identifique-o mais tarde.
    instance.add_tag(tag)


    # A instância está em execução agora, vamos tentar programaticamente
    # SSH para a instância usando o Paramiko via boto CmdShell.

    if cmd_shell:
        key_path = os.path.join(os.path.expanduser(key_dir),
                                key_name + key_extension)
        cmd = boto.manage.cmdshell.sshclient_from_instance(instance,
                                                           key_path,
                                                           user_name=login_user)

    return (instance, cmd)
